import { isAxiosError } from "axios";
import { ApiErrorData, ERROR_MESSAGES, ErrorHelp } from "@/lib/error-messages";

function getErrorData(error: unknown): ApiErrorData | undefined {
  if (!isAxiosError<ApiErrorData>(error)) return undefined;
  return error.response?.data ?? undefined;
}

export function getErrorCode(error: unknown): string | undefined {
  return getErrorData(error)?.code;
}

function getErrorCopy(code: string | undefined) {
  return code && Object.prototype.hasOwnProperty.call(ERROR_MESSAGES, code)
    ? ERROR_MESSAGES[code]
    : undefined;
}

export function getErrorHelp(error: unknown): ErrorHelp | undefined {
  return getErrorCopy(getErrorCode(error))?.help;
}

function getFrontendMessage(data: ApiErrorData): string | undefined {
  const copy = getErrorCopy(data.code);
  if (!copy) return undefined;
  return typeof copy.message === "function" ? copy.message(data) : copy.message;
}

export function getErrorMessage(error: unknown): string {
  if (isAxiosError<ApiErrorData>(error)) {
    if (error.response) {
      const data = error.response.data;
      return (
        (data && getFrontendMessage(data)) ||
        data?.message ||
        "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
      );
    }

    if (error.request) {
      return "서버에 연결할 수 없습니다. 인터넷 연결을 확인해 주세요.";
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.";
}
