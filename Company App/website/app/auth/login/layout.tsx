import { cookies } from "next/headers";
import jwt from "jsonwebtoken";
import { redirect } from "next/navigation";

async function getUser() {
  const token = (await cookies()).get("token")?.value;
  if (!token) return null;

  try {
    return jwt.verify(token, process.env.JWT_SECRET!) as {
      id: string;
      name: string;
      role: string;
    };
  } catch {
    return null;
  }
}

export default async function LoginLayout({ children }: { children: React.ReactNode }) {
  const user = await getUser();

  if (user?.role === "admin") redirect("/admin/dashboard");
  if (user?.role === "staff") redirect("/staff/dashboard");
  

  return <>{children}</>;
}
