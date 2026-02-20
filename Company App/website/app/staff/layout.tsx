import { cookies } from "next/headers";
import jwt from "jsonwebtoken";
import { redirect } from "next/navigation";

async function getUser() {
  const token = (await cookies()).get("token")?.value;
  if (!token) return null;

  try {
    const user = jwt.verify(token, process.env.JWT_SECRET!);
    return user as { id: string; name: string; role: string };
  } catch {
    return null;
  }
}

export default async function StaffLayout({ children }: { children: React.ReactNode }) {
  const user = await getUser();

  if (!user) redirect("/auth/login");
  if (user.role !== "staff") redirect("/auth/login");

  return <>{children}</>;
}
