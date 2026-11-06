"use client";

import React from "react";
import {
  useController,
  Control,
  FieldPathByValue,
  FieldValues,
  UseControllerProps,
} from "react-hook-form";

import {
  BaseInput,
  CheckboxInput,
  ColorInput,
  SelectInput,
  TextareaInput,
} from "./forms";

export interface Option {
  label: string;
  value: string;
}

interface CommonInputProps {
  name: string;
  label: string;
  placeholder?: string;
  helperText?: React.ReactNode;
  disabled?: boolean;
  required?: boolean;
  errorMessage?: string;
}

interface StringInputProps extends CommonInputProps {
  value: string;
  onChange: (value: string) => void;
}

export interface TextInputProps extends StringInputProps {
  type: "text" | "textarea" | "color";
}

export interface SelectInputProps extends StringInputProps {
  type: "select";
  options: readonly Option[];
  isLoading?: boolean;
}

export interface CheckboxInputProps extends CommonInputProps {
  type: "checkbox";
  value: boolean;
  onChange: (value: boolean) => void;
}

export type BasicInputProps =
  | TextInputProps
  | SelectInputProps
  | CheckboxInputProps;

export type InputTypes = BasicInputProps["type"];

export const BasicInput = (props: BasicInputProps) => {
  const content = () => {
    switch (props.type) {
      case "text":
        return <BaseInput {...props} />;
      case "textarea":
        return <TextareaInput {...props} />;
      case "checkbox":
        return <CheckboxInput {...props} />;
      case "select":
        return <SelectInput {...props} />;
      case "color":
        return <ColorInput {...props} />;
    }
  };

  return <div className="flex w-full flex-col">{content()}</div>;
};

type ControlledProps<P extends BasicInputProps> = Omit<
  P,
  "name" | "value" | "onChange" | "errorMessage" | "required"
>;

interface ControllerProps<T extends FieldValues, V> {
  control: Control<T>;
  name: FieldPathByValue<T, V>;
  rules?: UseControllerProps<T>["rules"];
}

type InputProps<T extends FieldValues> =
  | (ControlledProps<TextInputProps> & ControllerProps<T, string>)
  | (ControlledProps<SelectInputProps> & ControllerProps<T, string>)
  | (ControlledProps<CheckboxInputProps> & ControllerProps<T, boolean>);

export const Input = <T extends FieldValues>(props: InputProps<T>) => {
  const { control, name, rules, ...rest } = props;
  const {
    field: { value, onChange },
    fieldState: { error },
  } = useController<T>({ name, rules, control });

  const fieldProps = {
    name,
    required: Boolean(rules?.required),
    errorMessage: error?.message,
    onChange,
  };

  if (rest.type === "checkbox") {
    return <BasicInput {...rest} {...fieldProps} value={Boolean(value)} />;
  }
  return <BasicInput {...rest} {...fieldProps} value={value ?? ""} />;
};
