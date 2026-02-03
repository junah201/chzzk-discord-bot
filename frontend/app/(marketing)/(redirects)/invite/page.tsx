import { BOT_INVITE_URL } from "@/constants/links";
import { redirect } from "next/navigation";

export default function InviteRedirectPage() {
  redirect(BOT_INVITE_URL);
}
