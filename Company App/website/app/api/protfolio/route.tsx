import { NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export async function GET() {
    const [
      portfolio,
      contact
    ] = await Promise.all([
      
      prisma.portfolio.findMany(),
      prisma.contact.findFirst()
    ]);
    return NextResponse.json({ portfolio,contact});
}