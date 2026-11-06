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

  const labelId = `${name}-label`;
  const descriptionId = `${name}-description`;

  return (
    <FieldLabel>
      <Field orientation="horizontal">
        <Checkbox
          id={name}
          name={name}
          checked={value}
          onCheckedChange={onChange}
          aria-labelledby={label ? labelId : undefined}
          aria-describedby={descriptionId}
          aria-required={required}
          {...rest}
        />
        <FieldContent>
          {label && (
            <FieldTitle id={labelId}>
              {label} {required ? "*" : ""}
            </FieldTitle>
          )}
          {Boolean(errorMessage) ? (
            <FieldError id={descriptionId}>
              {errorMessage} {helperText}
            </FieldError>
          ) : (
            <FieldDescription id={descriptionId}>{helperText}</FieldDescription>
          )}
        </FieldContent>
      </Field>
    </FieldLabel>
  );
};
