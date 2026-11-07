"use client";

import { flushSync } from "react-dom";
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

  const insert = (button: HTMLElement, key: string) => {
    const text = `{${key}}`;
    // 추가 폼과 수정 다이얼로그가 함께 열려 있을 수 있어 같은 폼의 입력란을 찾는다.
    const textarea =
      button
        .closest("form")
        ?.querySelector<HTMLTextAreaElement>(
          'textarea[name="custom_message"]',
        ) ?? null;
    const focused = textarea !== null && document.activeElement === textarea;
    const start = focused ? textarea.selectionStart : message.length;
    const end = focused ? textarea.selectionEnd : message.length;
    flushSync(() =>
      onChange(message.slice(0, start) + text + message.slice(end)),
    );
    textarea?.focus();
    textarea?.setSelectionRange(start + text.length, start + text.length);
  };

  return (
    <div className="-mt-2 flex flex-col gap-1.5">
      <div className="flex flex-wrap gap-1.5">
        {MESSAGE_VARIABLES.map((variable) => (
          <button
            key={variable.key}
            type="button"
            onMouseDown={(e) => e.preventDefault()}
            onClick={(e) => insert(e.currentTarget, variable.key)}
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
