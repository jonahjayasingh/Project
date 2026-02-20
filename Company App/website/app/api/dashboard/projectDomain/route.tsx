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
    const description = formData.get("description");
   
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
    const safeName = name.toString().replace(/\s+/g, "_");
    const filename = `${safeName}${ext}`;

    const folder = path.join(process.cwd(), "public", "domains");
    await fs.promises.mkdir(folder, { recursive: true });

    const filePath = path.join(folder, filename);
    await fs.promises.writeFile(filePath, buffer);

    const course = await prisma.projectDomain
    .create({
      data: {
        name: name.toString(),
        description: (description ?? "").toString(),
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


export async function GET(req: NextRequest) {
  try {
    const courses = await prisma.projectDomain.findMany();
    return NextResponse.json(courses, { status: 200 });
  } catch (err) {
    console.error("Fetch error:", err);
    return NextResponse.json(
      { error: "Unexpected error while fetching courses" },
      { status: 500 }
    );
  }
}
