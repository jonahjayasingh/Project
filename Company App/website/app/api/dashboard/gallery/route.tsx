import { NextRequest, NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";
import jwt from "jsonwebtoken";
import fs from "fs";
import path from "path";


export const runtime = "nodejs";

const prisma = new PrismaClient();

export async function POST(req: NextRequest) {
    try {
        // ----------- AUTH / ROLE CHECK -----------
        const token = req.cookies.get("token")?.value;
        if (!token) {
            return NextResponse.json(
                { error: "Not authenticated" },
                { status: 401 }
            );
        }

        let decoded;
        try {
            decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
                id: string;
                name: string;
                role: string;
            };
        } catch {
            return NextResponse.json(
                { error: "Invalid or expired token" },
                { status: 401 }
            );
        }



        if (decoded.role !== "admin") {
            return NextResponse.json(
                { error: "You are not allowed to add gallery" },
                { status: 403 }
            );
        }
        // -----------------------------------------

        const formData = await req.formData();

        const title = formData.get("title");

        if (typeof title !== "string" || !title) {
            return NextResponse.json(
                { error: "title is required" },
                { status: 400 }
            );
        }

        const file = formData.get("image");
        if (!(file instanceof File)) {
            return NextResponse.json(
                { error: "image file is required" },
                { status: 400 }
            );
        }

        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);

        const originalName = file.name || "";
        const ext =
            originalName.lastIndexOf(".") !== -1
                ? originalName.slice(originalName.lastIndexOf("."))
                : "";

        const folder = path.join(process.cwd(), "public", "gallery");
        await fs.promises.mkdir(folder, { recursive: true });
        const file_name = `${title}${new Date().getTime()}${ext}`;
        const filePath = path.join(folder, file_name);
        await fs.promises.writeFile(filePath, buffer);

        const course = await prisma.gallery.create({
            data: {
                title: title,
                image: file_name,
                userId: Number(decoded.id),
            },
        });

        return NextResponse.json(course, { status: 200 });
    } catch (err) {
        console.error("Upload error:", err);
        return NextResponse.json(
            { error: "Unexpected error while uploading" },
            { status: 500 }
        );
    }
}


export async function PUT(req: NextRequest) {
  try {
    const token = req.cookies.get("token")?.value;
    if (!token) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    let decoded;
    try {
      decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
        id: string;
        role: string;
      };
    } catch {
      return NextResponse.json({ error: "Invalid or expired token" }, { status: 401 });
    }

    if (decoded.role !== "admin") {
      return NextResponse.json({ error: "Permission denied" }, { status: 403 });
    }

    const formData = await req.formData();
    const galleryId = Number(formData.get("id")); // ID comes from form-data
    if (!galleryId) {
      return NextResponse.json({ error: "Gallery ID missing" }, { status: 400 });
    }

    const title = String(formData.get("title") ?? "");
    const imageFile = formData.get("image") as File | null;

    let updateData: any = { title };

    // Add new image only if user uploaded one
    if (imageFile && imageFile.size > 0) {
      const buffer = Buffer.from(await imageFile.arrayBuffer());
      const newName = Date.now() + "-" + imageFile.name;

      const fs = require("fs");
      const uploadPath = `public/gallery/${newName}`;
      fs.writeFileSync(uploadPath, buffer);

      updateData.image = newName;
    }

    const updated = await prisma.gallery.update({
      where: { id: galleryId },
      data: updateData,
    });

    return NextResponse.json(
      { message: "Gallery updated successfully", data: updated },
      { status: 200 }
    );
  } catch (err) {
    console.error("PUT Gallery Error:", err);
    return NextResponse.json(
      { error: "Unexpected server error" },
      { status: 500 }
    );
  }
}



export async function DELETE(req: NextRequest) {
  try {
    const token = req.cookies.get("token")?.value;
    if (!token)
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });

    let decoded;
    try {
      decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
        id: string;
        role: string;
      };
    } catch {
      return NextResponse.json({ error: "Invalid or expired token" }, { status: 401 });
    }

    if (decoded.role !== "admin")
      return NextResponse.json({ error: "Permission denied" }, { status: 403 });

    const formData = await req.formData();
    const galleryId = Number(formData.get("id"));   // 👈 ID received from form-data

    if (!galleryId)
      return NextResponse.json({ error: "Gallery ID required" }, { status: 400 });

    // fetch record to locate image
    const gallery = await prisma.gallery.findUnique({ where: { id: galleryId } });
    if (!gallery)
      return NextResponse.json({ error: "Gallery not found" }, { status: 404 });

    // delete from DB
    await prisma.gallery.delete({ where: { id: galleryId } });

    // delete image from filesystem
    if (gallery.image) {
      const filePath = path.join(process.cwd(), "public", "gallery", gallery.image);
      if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    }

    return NextResponse.json({ message: "Gallery deleted successfully" }, { status: 200 });

  } catch (err) {
    console.error("DELETE Gallery Error:", err);
    return NextResponse.json(
      { error: "Unexpected server error" },
      { status: 500 }
    );
  }
}
