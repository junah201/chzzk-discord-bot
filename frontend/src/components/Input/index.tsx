import { Box } from '@mui/material';
import { useController, Control } from 'react-hook-form';

import { TextInput, SelectInput, MultilineInput } from './form';

import { RegisterTypes } from '@/constants/form';
import { FormRules, INPUT_TYPE, InputTypes, Option } from '@/types';

interface InitInputProps<RegisterTypes extends string> {
  name: RegisterTypes;
  label: string;
  type: InputTypes;
  placeholder?: string;
  helperText?: string;
  options?: Option[];
  disabled?: boolean;
}

interface BasicInputProps<RegisterTypes extends string>
  extends InitInputProps<RegisterTypes> {
  value: any;
  onChange: (...event: any[]) => void;
  errorMessage?: string | undefined;
}

interface ControlInputProps<RegisterTypes extends string>
  extends InitInputProps<RegisterTypes> {
  rules?: FormRules;
  control: Control<any, any>;
}

export const BasicInput = <RegisterTypes extends string>({
  name,
  label,
  type,
  value,
  onChange,
  placeholder = '',
  helperText = ' ',
  errorMessage = '',
  disabled = false,
  options = [],
}: BasicInputProps<RegisterTypes>) => {
  const content = (inputType: InputTypes) => {
    switch (inputType) {
      case INPUT_TYPE.TEXT:
        return (
          <TextInput
            name={name}
            label={label}
            value={value}
            onChange={onChange}
            placeholader={placeholder}
            errorMessage={errorMessage}
            helperText={helperText}
            disabled={disabled}
          />
        );
      case INPUT_TYPE.MULTILINE:
        return (
          <MultilineInput
            name={name}
            label={label}
            value={value}
            onChange={onChange}
            placeholader={placeholder}
            errorMessage={errorMessage}
            helperText={helperText}
            disabled={disabled}
          />
        );
      case INPUT_TYPE.SELECT:
        return (
          <SelectInput
            name={name}
            label={label}
            value={value}
            onChange={onChange}
            errorMessage={errorMessage}
            helperText={helperText}
            options={options}
            disabled={disabled}
          />
        );
    }
  };

  return (
    <Box
      sx={{
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {content(type)}
    </Box>
  );
};

export const ControlInput = <RegisterTypes extends string>({
  name,
  label,
  rules = {},
  type,
  control,
  placeholder = '',
  helperText = ' ',
  options = [],
  disabled = false,
}: ControlInputProps<RegisterTypes>) => {
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
      name={name}
      label={`${label} ${rules?.required ? '*' : ''}`}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      helperText={helperText}
      errorMessage={error?.message}
      disabled={disabled}
      options={options}
    />
  );
};
