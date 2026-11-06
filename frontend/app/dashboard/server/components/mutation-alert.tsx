import Link from "next/link";
import { ArrowRight, ExternalLink } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { getErrorHelp, getErrorMessage } from "@/lib/api-error";
import { ErrorHelp } from "@/lib/error-messages";
import { Notification } from "@/types/api";

export interface Feedback {
  variant: "success" | "destructive";
  title: string;
  description?: string;
  help?: ErrorHelp;
}

export function getNotificationLabel(n: Notification) {
  return `${n.chzzk_name || n.chzzk_id} → #${n.channel_name || n.channel_id}`;
}

export function ErrorHelpLink({ help }: { help: ErrorHelp }) {
  const className =
    "mt-2 flex w-fit items-center gap-1 font-medium underline underline-offset-2";

  if (help.external) {
    return (
      <a
        href={help.href}
        target="_blank"
        rel="noopener noreferrer"
        className={className}
      >
        {help.label}
        <ExternalLink className="h-3.5 w-3.5" />
      </a>
    );
  }

  return (
    <Link href={help.href} className={className}>
      {help.label}
      <ArrowRight className="h-3.5 w-3.5" />
    </Link>
  );
}

interface MutationAlertProps {
  error: unknown;
  isSuccess?: boolean;
  errorTitle?: string;
  successMessage?: string;
  onClose?: () => void;
  className?: string;
}

export default function MutationAlert({
  error,
  isSuccess = false,
  errorTitle = "요청을 처리하지 못했습니다",
  successMessage,
  onClose,
  className,
}: MutationAlertProps) {
  if (error) {
    const help = getErrorHelp(error);
    return (
      <Alert variant="destructive" onClose={onClose} className={className}>
        <AlertTitle>{errorTitle}</AlertTitle>
        <AlertDescription className="whitespace-pre-line">
          {getErrorMessage(error)}
          {help && <ErrorHelpLink help={help} />}
        </AlertDescription>
      </Alert>
    );
  }

  if (isSuccess && successMessage) {
    return (
      <Alert variant="success" onClose={onClose} className={className}>
        <AlertTitle>{successMessage}</AlertTitle>
      </Alert>
    );
  }

  return null;
}
