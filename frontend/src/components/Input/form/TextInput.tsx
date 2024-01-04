import { TextField, Tooltip } from '@mui/material';

interface TextInputProps {
  name: string;
  label: string;
  value: string;
  onChange: (...event: any[]) => void;
  placeholader: string;
  errorMessage: string | undefined;
  helperText: string | undefined;
  disabled: boolean;
}

export const TextInput = ({
  name,
  label,
  value,
  onChange,
  placeholader,
  errorMessage,
  helperText,
  disabled,
}: TextInputProps) => {
  return (
    <Tooltip
      title={(() => {
        if (disabled) {
          return '수정할 수 없습니다.';
        }
        return '';
      })()}
      placement="top-start"
    >
      <TextField
        id={name}
        label={label}
        value={value}
        onChange={onChange}
        placeholder={placeholader}
        fullWidth
        disabled={disabled}
        error={Boolean(errorMessage)}
        helperText={errorMessage || helperText}
        variant="outlined"
        size="medium"
      />
    </Tooltip>
  );
};
