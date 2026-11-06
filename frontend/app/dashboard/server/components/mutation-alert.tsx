import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { getErrorMessage } from "@/lib/api-error";
import { Notification } from "@/types/api";

export interface Feedback {
  variant: "success" | "destructive";
  title: string;
  description?: string;
  showTestGuide?: boolean;
}

export function getNotificationLabel(n: Notification) {
  return `${n.chzzk_name || n.chzzk_id} → #${n.channel_name || n.channel_id}`;
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
    return (
      <Alert variant="destructive" onClose={onClose} className={className}>
        <AlertTitle>{errorTitle}</AlertTitle>
        <AlertDescription className="whitespace-pre-line">
          {getErrorMessage(error)}
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
