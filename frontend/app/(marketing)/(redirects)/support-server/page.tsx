import { redirect } from "next/navigation";
import { SUPPORT_SERVER_INVITE_URL } from "@/constants/links";

export default function SupportServerRedirectPage() {
  redirect(SUPPORT_SERVER_INVITE_URL);
}
