import { NextRequest, NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";
import jwt from "jsonwebtoken";

export const runtime = "nodejs";
const prisma = new PrismaClient();

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
        { error: "You are not allowed to add contacts" },
        { status: 403 }
      );

    }

    const formData = await req.formData();

    const phone1 = String(formData.get("phone1") ?? "");
    const phone2 = String(formData.get("phone2") ?? "");
    const email = String(formData.get("email") ?? "");
    const map = String(formData.get("map") ?? "");
    const address = String(formData.get("address") ?? "");
    const instagram_link = String(formData.get("instagram_link") ?? "");
    const facebook_link = String(formData.get("facebook_link") ?? "");
    const X_link = String(formData.get("x_link") ?? "");
    const linkedin_link = String(formData.get("linkedin_link") ?? "");
    const youtube_link = String(formData.get("youtube_link") ?? "");
    console.log("error",address)
    const contact = await prisma.contact.upsert({
      where: { userId: Number(decoded.id) },
      update: {
        phone1,
        phone2,
        email,
        map,
        address,
        instagram_link,
        facebook_link,
        X_link,
        linkedin_link,
        youtube_link,
      },
      create: {
        phone1,
        phone2,
        email,
        map,
        address,               // 🔥 added (required!)
        instagram_link,
        facebook_link,
        X_link,
        linkedin_link,
        youtube_link,
        user: {
          connect: { id: Number(decoded.id) },
        },
      },
    });

    return NextResponse.json(contact, { status: 200 });
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
    const contactId = Number(formData.get("id")); // 🔥 coming from form data

    if (!contactId) {
      return NextResponse.json({ error: "Contact ID is required" }, { status: 400 });
    }

    const updated = await prisma.contact.update({
      where: { id: contactId },
      data: {
        phone1: String(formData.get("phone1") ?? ""),
        phone2: String(formData.get("phone2") ?? ""),
        email: String(formData.get("email") ?? ""),
        map: String(formData.get("map") ?? ""),
        address: String(formData.get("address") ?? ""),
        instagram_link: String(formData.get("instagram_link") ?? ""),
        facebook_link: String(formData.get("facebook_link") ?? ""),
        X_link: String(formData.get("x_link") ?? ""),
        linkedin_link: String(formData.get("linkedin_link") ?? ""),
        youtube_link: String(formData.get("youtube_link") ?? ""),
      },
    });

    return NextResponse.json(
      { message: "Contact updated successfully", data: updated },
      { status: 200 }
    );
  } catch (err) {
    console.error("PUT error:", err);
    return NextResponse.json(
      { error: "Unexpected server error" },
      { status: 500 }
    );
  }
}


