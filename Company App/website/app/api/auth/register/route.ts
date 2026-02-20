import { PrismaClient } from "@prisma/client";
import bcrypt from "bcryptjs";

export async function POST(req: Request) {
  const prisma = new PrismaClient();

  try {
    const { name, email, password, role = "user" } = await req.json();

    // Duplicate checks...  
    const existingEmail = await prisma.user.findUnique({ where: { email } });
    if (existingEmail) {
      return new Response(JSON.stringify({ error: "Email already exists" }), {
        status: 400,
      });
    }

    const existingName = await prisma.user.findUnique({ where: { name } });
    if (existingName) {
      return new Response(JSON.stringify({ error: "Name already exists" }), {
        status: 400,
      });
    }

    const hashedPassword = await bcrypt.hash(password, 10);



    const user = await prisma.user.create({
      data: { name, email, password: hashedPassword, role },
    });

    return new Response(JSON.stringify(user), { status: 201 });
  } catch (e) {
    console.error(e);
    return new Response(JSON.stringify({ error: "Unable to create user" }), {
      status: 500,
    });
  }
}




export async function PUT(req: Request) {
  const prisma = new PrismaClient();
  try {
    const { id, name, email, password, role } = await req.json();

    if (!id) {
      return new Response(JSON.stringify({ error: "User ID is required" }), {
        status: 400,
      });
    }

    // Fetch the existing user
    const existingUser = await prisma.user.findUnique({ where: { id } });
    if (!existingUser) {
      return new Response(JSON.stringify({ error: "User not found" }), {
        status: 404,
      });
    }

    // Unique email check
    if (email) {
      const existingEmail = await prisma.user.findUnique({ where: { email } });
      if (existingEmail && existingEmail.id !== id) {
        return new Response(JSON.stringify({ error: "Email already exists" }), {
          status: 400,
        });
      }
    }

    // Unique name check
    if (name) {
      const existingName = await prisma.user.findUnique({ where: { name } });
      if (existingName && existingName.id !== id) {
        return new Response(JSON.stringify({ error: "Name already exists" }), {
          status: 400,
        });
      }
    }


    // Build update object dynamically
    const updateData: any = {
      name: name ?? existingUser.name,
      email: email ?? existingUser.email,
      role: role ?? existingUser.role,
    };

    // Only update password if provided
    if (password && password.trim() !== "") {
      updateData.password = await bcrypt.hash(password, 10);
    }

    const user = await prisma.user.update({
      where: { id },
      data: updateData,
    });

    return new Response(JSON.stringify({ message: "User updated successfully" } ), { status: 200 });

  } catch (e) {
    console.error(e);
    return new Response(JSON.stringify({ error: "Unable to update user" }), {
      status: 500,
    });
  }
}
