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

    const courseName = formData.get("course_name");
    const description = formData.get("description");
    const duration = formData.get("duration");
    const price = formData.get("Price");
    const difficulty = formData.get("course_difficulty");

    if (typeof courseName !== "string" || !courseName) {
      return NextResponse.json(
        { error: "course_name is required" },
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
    const safeName = courseName.replace(/\s+/g, "_");
    const filename = `${safeName}${ext}`;

    const folder = path.join(process.cwd(), "public", "courses");
    await fs.promises.mkdir(folder, { recursive: true });

    const filePath = path.join(folder, filename);
    await fs.promises.writeFile(filePath, buffer);

    const course = await prisma.courses.create({
      data: {
        course_name: courseName,
        description: (description ?? "").toString(),
        duration: (duration ?? "").toString(),
        Price: (price ?? "").toString(),
        course_difficulty: (difficulty ?? "Beginner") as any,
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
      return NextResponse.json({ error: "Course id required" }, { status: 400 });
    }

    const courseName = formData.get("course_name");
    const description = formData.get("description");
    const duration = formData.get("duration");
    const price = formData.get("Price");
    const difficulty = formData.get("course_difficulty");
    const file = formData.get("image");

    // Fetch existing course
    const existingCourse = await prisma.courses.findUnique({
      where: { id: Number(id) },
    });

    if (!existingCourse) {
      return NextResponse.json({ error: "Course not found" }, { status: 404 });
    }

    let filename = existingCourse.image; // default

    // -------- IMAGE UPLOAD LOGIC + REMOVE OLD FILE --------
    if (file instanceof File) {
      const bytes = await file.arrayBuffer();
      const buffer = Buffer.from(bytes);

      const originalName = file.name || "";
      const ext =
        originalName.lastIndexOf(".") !== -1
          ? originalName.slice(originalName.lastIndexOf("."))
          : "";

      const safeName = String(courseName ?? existingCourse.course_name).replace(/\s+/g, "_");
      filename = `${safeName}${ext}`;

      const folder = path.join(process.cwd(), "public", "courses");
      await fs.promises.mkdir(folder, { recursive: true });

      const newPath = path.join(folder, filename);
      await fs.promises.writeFile(newPath, buffer);

      // ❗ DELETE OLD IMAGE if different
      if (existingCourse.image && existingCourse.image !== filename) {
        const oldPath = path.join(folder, existingCourse.image);

        fs.promises
          .unlink(oldPath)
          .catch(() => console.warn("Old image not found, skipping delete"));
      }
    }
    // -------------------------------------------------------

    const updatedCourse = await prisma.courses.update({
      where: { id: Number(id) },
      data: {
        course_name: (courseName ?? existingCourse.course_name).toString(),
        description: (description ?? existingCourse.description).toString(),
        duration: (duration ?? existingCourse.duration).toString(),
        Price: (price ?? existingCourse.Price).toString(),
        course_difficulty: (difficulty ?? existingCourse.course_difficulty) as any,
        image: filename,
      },
    });

    return NextResponse.json(updatedCourse, { status: 200 });
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
    const courseId = Number(formData.get("id"));   

    if (!courseId)
      return NextResponse.json({ error: "Course ID required" }, { status: 400 });

    // fetch record to locate image
    const courses = await prisma.courses.findUnique({ where: { id: courseId } });
    if (!courses)
      return NextResponse.json({ error: "Course not found" }, { status: 404 });

    // delete from DB
    await prisma.courses.delete({ where: { id: courseId } });

    // delete image from filesystem
    if (courses.image) {
      const filePath = path.join(process.cwd(), "public", "courses", courses.image);
      if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    }

    return NextResponse.json({ message: "Course deleted successfully" }, { status: 200 });

  } catch (err) {
    console.error("DELETE Course Error:", err);
    return NextResponse.json(
      { error: "Unexpected server error" },
      { status: 500 }
    );
  }
}
