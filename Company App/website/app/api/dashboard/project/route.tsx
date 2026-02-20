import { NextRequest, NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";
import jwt from "jsonwebtoken";

export const runtime = "nodejs";
const prisma = new PrismaClient();

// CREATE PROJECT
export async function POST(req: NextRequest) {
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
      return NextResponse.json(
        { error: "You are not allowed to add projects" },
        { status: 403 }
      );
    }

    const formData = await req.formData();
    
    const title = formData.get("title");
    const description = formData.get("description");
    const domainid = formData.get("domainid");

    if (!title || typeof title !== "string") {
      return NextResponse.json({ error: "Title is required" }, { status: 400 });
    }
    if (!domainid) {
      return NextResponse.json({ error: "Domain is required" }, { status: 400 });
    }

    const newProject = await prisma.project.create({
      data: {
        title,
        description: description?.toString() ?? "",
        domainid: Number(domainid),
        userId: Number(decoded.id),
      },
    });

    return NextResponse.json(newProject, { status: 200 });
  } catch (err) {
    console.error("Project create error:", err);
    return NextResponse.json(
      { error: "Unexpected error while creating project" },
      { status: 500 }
    );
  }
}

// UPDATE PROJECT
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
      return NextResponse.json(
        { error: "You are not allowed to edit projects" },
        { status: 403 }
      );
    }

    const formData = await req.formData();
    const id = formData.get("id");

    if (!id) {
      return NextResponse.json({ error: "Project id is required" }, { status: 400 });
    }

    const existing = await prisma.project.findUnique({
      where: { id: Number(id) },
    });

    if (!existing) {
      return NextResponse.json({ error: "Project not found" }, { status: 404 });
    }

    const title = formData.get("title") ?? existing.title;
    const description = formData.get("description") ?? existing.description;
    const domainid = formData.get("domainid") ?? existing.domainid;

    const updated = await prisma.project.update({
      where: { id: Number(id) },
      data: {
        title: title.toString(),
        description: description.toString(),
        domainid: Number(domainid),
      },
    });

    return NextResponse.json(updated, { status: 200 });
  } catch (err) {
    console.error("Project update error:", err);
    return NextResponse.json(
      { error: "Unexpected error while updating project" },
      { status: 500 }
    );
  }
}



