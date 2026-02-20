import { NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export async function GET() {
    const [
      courses,
      gallerys,
      placements,
      contact
    ] = await Promise.all([
      prisma.courses.findMany(),
      prisma.gallery.findMany(),
      prisma.placement.findMany(),
      prisma.contact.findFirst()
    ]);
    return NextResponse.json({ courses, gallerys, placements, contact });
}