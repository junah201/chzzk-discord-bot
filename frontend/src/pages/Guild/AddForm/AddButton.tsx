import { Button } from '@mui/material';
import { UseFormHandleSubmit } from 'react-hook-form';

import { addNotification } from '@/api';
import { QUERY, RegisterField } from '@/constants';
import { useCustomMutation } from '@/lib';

interface AddButtonProps {
  handleSubmit: UseFormHandleSubmit<RegisterField, undefined>;
}

const AddButton = ({ handleSubmit }: AddButtonProps) => {
  const { mutate, isLoading } = useCustomMutation(
    (userInput) => addNotification(userInput),
    {
      SuccessMessage: '치지직 알림이 추가되었습니다.',
      SuccessQueryKey: QUERY.KEY.NOTIFICATIONS,
      ErrorMessage: '치지직 알림 추가에 실패했습니다.',
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
      치지직 알림 추가
    </Button>
  );
};

export default AddButton;
