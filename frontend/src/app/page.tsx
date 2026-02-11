import { redirect } from "next/navigation";

export default function HomePage() {
  // Redirect to dashboard by default
  // TODO: Check if profile is complete, redirect to /profile/edit if not
  redirect("/dashboard");
}
