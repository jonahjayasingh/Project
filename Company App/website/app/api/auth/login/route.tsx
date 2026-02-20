  import { PrismaClient } from "@prisma/client";
  import bcrypt from "bcryptjs";
  import jwt from "jsonwebtoken";

  const prisma = new PrismaClient();

  export async function POST(req: Request) {
    try {
      const { name, password } = await req.json();

      const user = await prisma.user.findUnique({ where: { name } });
      if (!user) {
        return new Response(JSON.stringify({ error: "Invalid name" }), { status: 400 });
      }

      const validPassword = await bcrypt.compare(password, user.password);
      if (!validPassword) {
        return new Response(JSON.stringify({ error: "Invalid password" }), { status: 400 });
      }

      // Create token
      const token = jwt.sign(
        { id: user.id, name: user.name, role: user.role },
        process.env.JWT_SECRET!,
        { expiresIn: "1d" }
      );
  const headers = new Headers();
  headers.append("Set-Cookie", `token=${token}; HttpOnly; Path=/; Max-Age=86400`);

  return new Response(
    JSON.stringify({
      message: "Login successful",
      token,
      role: user.role,
    }),
    {
      status: 200,
      headers,
    }
  );




    } catch (err) {
      console.error(err);
      return new Response(JSON.stringify({ error: "Login failed" }), { status: 500 });
    }
  }

export async function GET(req: Request) {
  const token = req.headers.get("token");

  if (!token) {
    return new Response(JSON.stringify({ error: "No token provided" }), { status: 400 });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as jwt.JwtPayload;

    return new Response(
      JSON.stringify({
        name: decoded.name,
        role: decoded.role,
      }),
      { status: 200 }
    );

  } catch (err) {
    return new Response(JSON.stringify({ error: "Invalid token" }), { status: 400 });
  }
}
