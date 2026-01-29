import { Button } from '@mui/material';
import { UseFormHandleSubmit } from 'react-hook-form';

import { updateNotification } from '@/api';
import { QUERY, RegisterField } from '@/constants';
import { useCustomMutation } from '@/lib';

interface UpdateButtonProps {
  handleSubmit: UseFormHandleSubmit<RegisterField, undefined>;
}

const UpdateButton = ({ handleSubmit }: UpdateButtonProps) => {
  const { mutate, isLoading } = useCustomMutation(
    (userInput) => updateNotification(userInput),
    {
      SuccessMessage: `수정되었습니다.`,
      SuccessQueryKey: QUERY.KEY.NOTIFICATIONS,
      ErrorMessage: `수정에 실패했습니다.`,
    }
  );

  return (
    <Button
      onClick={handleSubmit((userInput) => mutate(userInput))}
      disabled={isLoading}
      disableElevation
      fullWidth
      variant="contained"
      color="primary"
    >
      수정하기
    </Button>
  );
};

export default UpdateButton;
