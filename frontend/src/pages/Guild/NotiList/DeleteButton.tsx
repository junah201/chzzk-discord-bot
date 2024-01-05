import { DeleteForeverOutlined } from '@mui/icons-material';
import { IconButton, Tooltip } from '@mui/material';

import { deleteNotification } from '@/api';
import { QUERY } from '@/constants';
import { useCustomMutation } from '@/lib';

interface DeleteButtonProps {
  channel_id: string;
  chzzk_id: string;
}

const DeleteButton = ({ channel_id, chzzk_id }: DeleteButtonProps) => {
  const { mutate, isLoading } = useCustomMutation(
    () =>
      deleteNotification({
        channel_id,
        chzzk_id,
      }),
    {
      SuccessMessage: `${chzzk_id} 알림이 삭제되었습니다.`,
      SuccessQueryKey: QUERY.KEY.NOTIFICATIONS,
      ErrorMessage: `${chzzk_id} 알림 삭제에 실패했습니다.`,
    }
  );

  return (
    <Tooltip title="삭제하기" placement="top" arrow>
      <span>
        <IconButton onClick={mutate} disabled={isLoading}>
          <DeleteForeverOutlined color="error" />
        </IconButton>
      </span>
    </Tooltip>
  );
};

export default DeleteButton;
