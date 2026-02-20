import { NextRequest, NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";
import jwt from "jsonwebtoken";

export const runtime = "nodejs";

const prisma = new PrismaClient();

export async function GET(req: NextRequest) {
  try {
    const token = req.cookies.get("token")?.value;
    if (!token) return NextResponse.json({ error: "Not authenticated" }, { status: 401 });

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
      return NextResponse.json({ error: "You are not allowed to add courses" }, { status: 403 });
    }

    const [
      courses,
      gallerys,
      projectDomains,
      projects,
      placements,
      contact
    ] = await Promise.all([
      prisma.courses.findMany(),
      prisma.gallery.findMany(),
      prisma.projectDomain.findMany(),
      prisma.project.findMany(),
      prisma.placement.findMany(),
      prisma.contact.findFirst()
    ]);

    return NextResponse.json(
      { courses, gallerys, projectDomains, projects, placements, contact },
      { status: 200 }
    );

  } catch (err) {
    console.error("API error:", err);
    return NextResponse.json({ error: "Unexpected error occurred" }, { status: 500 });
  }
}
