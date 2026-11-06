"use client";

import { useState } from "react";
import { HexColorPicker } from "react-colorful";
import { Check, RotateCcw } from "lucide-react";

import {
  Field,
  FieldDescription,
  FieldError,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  DEFAULT_EMBED_COLOR,
  toCssColor,
  toHexEmbedColor,
} from "@/lib/discord";
import { TextInputProps } from "..";

const DEFAULT_HEX = toCssColor(DEFAULT_EMBED_COLOR).toUpperCase();

const PRESET_COLORS = [
  "#5865F2",
  "#ED4245",
  "#F47B67",
  "#FEE75C",
  "#57F287",
  "#3BA55C",
  "#EB459E",
  "#FFFFFF",
];

export const ColorInput = (props: TextInputProps) => {
  const {
    name,
    errorMessage,
    label,
    helperText,
    required,
    disabled,
    value,
    onChange,
  } = props;

  const hex = toHexEmbedColor(value);
  const [draft, setDraft] = useState<string | null>(null);
  const displayHex = hex || DEFAULT_HEX;

  const handleTextChange = (text: string) => {
    const digits = text
      .replace(/[^0-9a-fA-F]/g, "")
      .slice(0, 6)
      .toUpperCase();
    setDraft(digits);
    if (digits.length === 6) onChange(`#${digits}`);
    else if (digits.length === 0) onChange("");
  };

  return (
    <Field>
      {label && (
        <FieldLabel htmlFor={name} aria-required={required}>
          {label} {required ? "*" : ""}
        </FieldLabel>
      )}
      <div className="flex gap-2">
        <Popover>
          <PopoverTrigger asChild>
            <button
              type="button"
              disabled={disabled}
              aria-label="색상 선택"
              className="size-9 shrink-0 rounded-md border border-border shadow-xs transition-[box-shadow] outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50"
              style={{ backgroundColor: displayHex }}
            />
          </PopoverTrigger>
          <PopoverContent
            align="start"
            className="flex w-60 flex-col gap-3 p-3"
          >
            <HexColorPicker
              color={displayHex}
              onChange={(color) => onChange(color.toUpperCase())}
              style={{ width: "100%", height: 160 }}
            />
            <div className="grid grid-cols-8 gap-1.5">
              {PRESET_COLORS.map((color) => (
                <button
                  key={color}
                  type="button"
                  aria-label={color}
                  onClick={() => onChange(color)}
                  className="flex aspect-square items-center justify-center rounded-sm border border-border outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  style={{ backgroundColor: color }}
                >
                  {hex === color && (
                    <Check className="size-3 text-white drop-shadow-[0_0_1px_rgb(0_0_0)]" />
                  )}
                </button>
              ))}
            </div>
            <button
              type="button"
              onClick={() => onChange("")}
              disabled={!hex}
              className="flex items-center justify-center gap-1.5 rounded-md border border-border px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground disabled:pointer-events-none disabled:opacity-50"
            >
              <RotateCcw className="size-3" />
              기본 색상으로 되돌리기
            </button>
          </PopoverContent>
        </Popover>
        <div className="relative flex-1">
          <span className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-sm text-muted-foreground">
            #
          </span>
          <Input
            id={name}
            name={name}
            disabled={disabled}
            aria-invalid={Boolean(errorMessage)}
            autoComplete="off"
            spellCheck={false}
            maxLength={7}
            className="pl-6 font-mono uppercase placeholder:font-sans"
            placeholder={`${DEFAULT_HEX.slice(1)} (기본 색상)`}
            value={draft ?? hex.slice(1)}
            onChange={(e) => handleTextChange(e.target.value)}
            onBlur={() => setDraft(null)}
          />
        </div>
      </div>
      {Boolean(errorMessage) ? (
        <FieldError>
          {errorMessage} {helperText}
        </FieldError>
      ) : (
        <FieldDescription>{helperText}</FieldDescription>
      )}
    </Field>
  );
};
