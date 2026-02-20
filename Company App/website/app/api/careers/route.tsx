import { NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export async function GET() {
  const [
    jobPosts,
    contact
  ] = await Promise.all([

    prisma.jobPost.findMany(),
    prisma.contact.findFirst()
  ]);
  return NextResponse.json({ jobPosts, contact });
}