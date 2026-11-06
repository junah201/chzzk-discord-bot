"use client";

import { Field, FieldDescription, FieldError } from "@/components/ui/field";
import { SelectInputProps } from "..";

import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export const SelectInput = (props: SelectInputProps) => {
  const {
    name,
    errorMessage,
    label,
    helperText,
    disabled,
    required,
    placeholder,
    options,
    value,
    onChange,
    ref,
    isLoading = false,
  } = props;

  return (
    <Field>
      {label && (
        <Label htmlFor={name}>
          {label} {required ? "*" : ""}
        </Label>
      )}
      <Select
        value={value}
        onValueChange={onChange}
        disabled={disabled || isLoading}
      >
        <SelectTrigger ref={ref} id={name} name={name} aria-busy={isLoading}>
          {isLoading ? (
            <span className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="size-4 animate-spin" />
              불러오는 중...
            </span>
          ) : (
            <SelectValue placeholder={placeholder} />
          )}
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
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
