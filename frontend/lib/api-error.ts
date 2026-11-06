import { isAxiosError } from "axios";

interface ApiErrorResponse {
  message: string;
}

export function getErrorMessage(error: unknown): string {
  if (isAxiosError<ApiErrorResponse>(error)) {
    if (error.response) {
      return (
        error.response.data?.message ||
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
