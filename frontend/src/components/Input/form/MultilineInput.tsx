import { TextField, Tooltip } from '@mui/material';

interface MultilineInputProps {
  name: string;
  label: string;
  value: string;
  onChange: (...event: any[]) => void;
  placeholader: string;
  errorMessage: string | undefined;
  helperText: string | undefined;
  disabled: boolean;
}

export const MultilineInput = ({
  name,
  label,
  value,
  onChange,
  placeholader,
  errorMessage,
  helperText,
  disabled,
}: MultilineInputProps) => {
  return (
    <Tooltip title="여러 줄 입력 가능합니다." placement="top-start">
      <TextField
        id={name}
        label={label}
        value={value}
        onChange={onChange}
        disabled={disabled}
        placeholder={placeholader}
        fullWidth
        error={Boolean(errorMessage)}
        helperText={errorMessage || helperText}
        variant="outlined"
        size="medium"
        multiline
        InputProps={{
          minRows: 2,
        }}
      />
    </Tooltip>
  );
};
