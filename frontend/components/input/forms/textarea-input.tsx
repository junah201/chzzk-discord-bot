"use client";

import {
  Field,
  FieldDescription,
  FieldError,
  FieldLabel,
} from "@/components/ui/field";
import { BasicInputProps } from "..";

import { Textarea } from "@/components/ui/textarea";

export const TextareaInput = (props: BasicInputProps) => {
  const { name, errorMessage, label, helperText, inputProps, rules, ...rest } =
    props;

  return (
    <Field>
      {label && (
        <FieldLabel
          htmlFor={name}
          aria-required={rules?.required ? true : false}
        >
          {label} {rules?.required ? "*" : ""}
        </FieldLabel>
      )}
      <Textarea id={name} name={name} {...rest} {...inputProps} />
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
