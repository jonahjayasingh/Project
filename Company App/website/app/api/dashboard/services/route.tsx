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

    const serviceName = formData.get("title");
    const description = formData.get("description");
    const keyPoints = formData.get("key_points");

    if (typeof serviceName !== "string" || !serviceName) {
      return NextResponse.json(
        { error: "service_name is required" },
        { status: 400 }
      );
    }
    const service = await prisma.services.create({
      data: {
        name: serviceName,
        description: (description ?? "").toString(),
        key_points: (keyPoints ?? "").toString(),
        userId: Number(decoded.id),
      },
    });

    return NextResponse.json(service, { status: 200 });
  } catch (err) {
    console.error("Upload error:", err);
    return NextResponse.json(
      { error: "Unexpected error while uploading" },
      { status: 500 }
    );
  }
}
