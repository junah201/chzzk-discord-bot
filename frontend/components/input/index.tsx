"use client";

import React from "react";
import { useController, Control, UseControllerProps } from "react-hook-form";

import { BaseInput, CheckboxInput, SelectInput, TextareaInput } from "./forms";

type Rules = UseControllerProps["rules"];
export interface Option {
  label: string;
  value: string;
}
export type InputTypes = "text" | "select" | "textarea" | "checkbox";

interface BaseInputProps {
  name: string;
  label: string;
  type: InputTypes;
  placeholder?: string;
  helperText?: string | React.ReactNode;
  options?: Option[] | readonly Option[];
  disabled?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  inputProps?: any;
  rules?: Rules;
}

export interface BasicInputProps extends BaseInputProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  value: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onChange: (...event: any[]) => void;
  errorMessage?: string | undefined;
}

export const BasicInput = (props: BasicInputProps) => {
  const { type } = props;

  const content = (inputType: InputTypes) => {
    switch (inputType) {
      case "text":
        return <BaseInput {...props} />;
      case "textarea":
        return <TextareaInput {...props} />;
      case "checkbox":
        return <CheckboxInput {...props} />;
      case "select":
        return <SelectInput {...props} />;
      default:
        return (
          <p>
            Invalid Input Type : <span className="font-bold">{props.type}</span>
          </p>
        );
    }
  };

  return <div className="flex w-full flex-col">{content(type)}</div>;
};

interface InputProps extends BaseInputProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  control: Control<any>;
}

export const Input = (props: InputProps) => {
  const { name, rules, control } = props;

  const {
    field: { value, onChange },
    fieldState: { error },
  } = useController({
    name,
    rules,
    control,
  });

  return (
    <BasicInput
      {...props}
      value={value}
      onChange={onChange}
      errorMessage={error?.message}
    />
  );
};
