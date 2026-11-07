"use client";

import { Control, useController } from "react-hook-form";
import {
  MESSAGE_VARIABLES,
  findUnknownVariables,
} from "@/lib/message-template";
import { NotificationFormValues } from "./notification-form";

interface MessageVariablePickerProps {
  control: Control<NotificationFormValues>;
}

/** 커스텀 메시지 입력란의 커서 위치에 변수를 넣는 버튼 목록 */
export default function MessageVariablePicker({
  control,
}: MessageVariablePickerProps) {
  const {
    field: { value, onChange },
  } = useController({ control, name: "custom_message" });
  const message = value ?? "";
  const unknown = findUnknownVariables(message);

  const insert = (key: string) => {
    const text = `{${key}}`;
    const textarea = document.getElementById(
      "custom_message",
    ) as HTMLTextAreaElement | null;
    const start = textarea?.selectionStart ?? message.length;
    const end = textarea?.selectionEnd ?? message.length;
    onChange(message.slice(0, start) + text + message.slice(end));
    requestAnimationFrame(() => {
      textarea?.focus();
      textarea?.setSelectionRange(start + text.length, start + text.length);
    });
  };

  return (
    <div className="-mt-2 flex flex-col gap-1.5">
      <div className="flex flex-wrap gap-1.5">
        {MESSAGE_VARIABLES.map((variable) => (
          <button
            key={variable.key}
            type="button"
            onClick={() => insert(variable.key)}
            title={`{${variable.key}}`}
            className="rounded-md border border-border bg-secondary/50 px-2 py-0.5 text-xs text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
          >
            {variable.label}
          </button>
        ))}
      </div>
      {unknown.length > 0 && (
        <p className="text-xs text-destructive">
          지원하지 않는 변수는 그대로 전송됩니다: {unknown.join(", ")}
        </p>
      )}
    </div>
  );
}
