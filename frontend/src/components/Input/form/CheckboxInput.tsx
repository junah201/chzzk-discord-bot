import {
  Checkbox,
  FormControl,
  FormControlLabel,
  FormHelperText,
} from '@mui/material';

interface CheckboxInputProps {
  name: string;
  label: string;
  value: boolean;
  onChange: (...event: any[]) => void;
  errorMessage: string | undefined;
  helperText: string | undefined;
  disabled: boolean;
}

export const CheckboxInput = ({
  name,
  label,
  value,
  onChange,
  errorMessage,
  helperText,
  disabled,
}: CheckboxInputProps) => {
  return (
    <>
      <FormControl error={Boolean(errorMessage)} fullWidth>
        <FormControlLabel
          control={
            <Checkbox
              checked={value}
              onChange={onChange}
              name={name}
              id={name}
              disabled={disabled}
            />
          }
          label={label}
        />
        <FormHelperText>{errorMessage || helperText}</FormHelperText>
      </FormControl>
    </>
  );
};
