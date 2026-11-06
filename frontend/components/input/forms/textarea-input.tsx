"use client";

import {
  Field,
  FieldDescription,
  FieldError,
  FieldLabel,
} from "@/components/ui/field";
import { TextInputProps } from "..";

import { Textarea } from "@/components/ui/textarea";

export const TextareaInput = (props: TextInputProps) => {
  const {
    name,
    errorMessage,
    label,
    helperText,
    placeholder,
    disabled,
    required,
    value,
    onChange,
    ref,
  } = props;

  return (
    <Field>
      {label && (
        <FieldLabel htmlFor={name}>
          {label} {required ? "*" : ""}
        </FieldLabel>
      )}
      <Textarea
        ref={ref}
        id={name}
        name={name}
        placeholder={placeholder}
        disabled={disabled}
        aria-required={required}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
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
