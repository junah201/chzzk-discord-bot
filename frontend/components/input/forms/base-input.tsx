"use client";

import {
  Field,
  FieldDescription,
  FieldError,
  FieldLabel,
} from "@/components/ui/field";
import { BasicInputProps } from "..";

import { Input } from "@/components/ui/input";

export const BaseInput = (props: BasicInputProps) => {
  const { name, errorMessage, label, helperText, inputProps, rules, ...rest } =
    props;

  return (
    <Field>
      {label && (
        <FieldLabel htmlFor={name}>
          {label} {rules?.required ? "*" : ""}
        </FieldLabel>
      )}
      <Input id={name} name={name} {...rest} {...inputProps} />
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
