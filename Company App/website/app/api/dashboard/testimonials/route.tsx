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
        { error: "You are not allowed to add courses" },
        { status: 403 }
      );
    }
    // -----------------------------------------

    const formData = await req.formData();

    const name = formData.get("name");
    const job_title = formData.get("job_title");
    const company_name = formData.get("company_name");

    if (typeof name !== "string" || !name) {
      return NextResponse.json(
        { error: "name is required" },
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
    const safeName = name.replace(/\s+/g, "_");
    const filename = `${safeName}${ext}`;

    const folder = path.join(process.cwd(), "public", "placements");
    await fs.promises.mkdir(folder, { recursive: true });

    const filePath = path.join(folder, filename);
    await fs.promises.writeFile(filePath, buffer);

    const course = await prisma.placement.create({
      data: {
        name: name.toString(),
        job_title: (job_title ?? "").toString(),
        company: (company_name ?? "").toString(),
        image: filename,
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
    // ----------- AUTH / ROLE CHECK -----------
    const token = req.cookies.get("token")?.value;
    if (!token) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    let decoded;
    try {
      decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
        id: string;
        name: string;
        role: string;
      };
    } catch {
      return NextResponse.json({ error: "Invalid or expired token" }, { status: 401 });
    }

    if (decoded.role !== "admin") {
      return NextResponse.json({ error: "You are not allowed to edit courses" }, { status: 403 });
    }
    // --------------------------------------------------

    const formData = await req.formData();

    const id = formData.get("id");
    if (!id) {
      return NextResponse.json({ error: "placements id required" }, { status: 400 });
    }

    const name = formData.get("name");
    const job_title = formData.get("job_title");
    const company_name = formData.get("company_name");
    const file = formData.get("image");
    // Fetch existing course
    const existingPlacement = await prisma.placement.findUnique({
      where: { id: Number(id) },
    });

    if (!existingPlacement) {
      return NextResponse.json({ error: "placements not found" }, { status: 404 });
    }

    let filename = existingPlacement.image; // default

    // -------- IMAGE UPLOAD LOGIC + REMOVE OLD FILE --------
    if (file instanceof File) {
      const bytes = await file.arrayBuffer();
      const buffer = Buffer.from(bytes);

      const originalName = file.name || "";
      const ext =
        originalName.lastIndexOf(".") !== -1
          ? originalName.slice(originalName.lastIndexOf("."))
          : "";

      const safeName = String(name ?? existingPlacement.name).replace(/\s+/g, "_");
      filename = `${safeName}${ext}`;

      const folder = path.join(process.cwd(), "public", "placements");
      await fs.promises.mkdir(folder, { recursive: true });

      const newPath = path.join(folder, filename);
      await fs.promises.writeFile(newPath, buffer);

      // ❗ DELETE OLD IMAGE if different
      if (existingPlacement.image && existingPlacement.image !== filename) {
        const oldPath = path.join(folder, existingPlacement.image);

        fs.promises
          .unlink(oldPath)
          .catch(() => console.warn("Old image not found, skipping delete"));
      }
    }
    // -------------------------------------------------------

    const updatedplacements = await prisma.placement.update({
      where: { id: Number(id) },
      data: {
        name: (name ?? existingPlacement.name).toString(),
        job_title: (job_title ?? existingPlacement.job_title).toString(),
        company: (company_name ?? existingPlacement.company).toString(),
        image: filename,
      },
    });

    return NextResponse.json(updatedplacements, { status: 200 });
  } catch (err) {
    console.error("Update error:", err);
    return NextResponse.json(
      { error: "Unexpected error while updating course" },
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
    const placementId = Number(formData.get("id"));   

    if (!placementId)
      return NextResponse.json({ error: "placements ID required" }, { status: 400 });

    // fetch record to locate image
    const courses = await prisma.placement.findUnique({ where: { id: placementId } });
    if (!courses)
      return NextResponse.json({ error: "placements not found" }, { status: 404 });

    // delete from DB
    await prisma.placement.delete({ where: { id: placementId } });

    // delete image from filesystem
    if (courses.image) {
      const filePath = path.join(process.cwd(), "public", "placements", courses.image);
      if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    }

    return NextResponse.json({ message: "placements deleted successfully" }, { status: 200 });

  } catch (err) {
    console.error("DELETE placements Error:", err);
    return NextResponse.json(
      { error: "Unexpected server error" },
      { status: 500 }
    );
  }
}
