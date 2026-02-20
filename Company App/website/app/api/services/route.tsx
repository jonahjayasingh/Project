import { NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export async function GET() {
    const [
      projectDomains,
      services,
      contact
    ] = await Promise.all([
      prisma.projectDomain.findMany({
        include: {
          project: true
        }
      }),
      prisma.services.findMany(),
      prisma.contact.findFirst()
    ]);
    return NextResponse.json({ projectDomains ,services,contact});
}