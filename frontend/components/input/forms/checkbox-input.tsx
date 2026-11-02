"use client";

import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldLabel,
  FieldTitle,
} from "@/components/ui/field";
import { BasicInputProps } from "..";

import { Checkbox } from "@/components/ui/checkbox";

export const CheckboxInput = (props: BasicInputProps) => {
  const {
    name,
    errorMessage,
    label,
    helperText,
    required,
    type,
    placeholder,
    value,
    onChange,
    ...rest
  } = props;

  return (
    <FieldLabel>
      <Field orientation="horizontal">
        <Checkbox
          id={name}
          name={name}
          checked={value}
          onCheckedChange={onChange}
          {...rest}
        />
        <FieldContent>
          {label && (
            <FieldTitle id={name} aria-required={required}>
              {label} {required ? "*" : ""}
            </FieldTitle>
          )}
          {Boolean(errorMessage) ? (
            <FieldError>
              {errorMessage} {helperText}
            </FieldError>
          ) : (
            <FieldDescription>{helperText}</FieldDescription>
          )}
        </FieldContent>
      </Field>
    </FieldLabel>
  );
};
