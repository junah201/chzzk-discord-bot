import { CreateOutlined } from '@mui/icons-material';
import { Tooltip, IconButton } from '@mui/material';
import { useConfirm } from 'material-ui-confirm';

import UpdateModal from './UpdateModal';

import { Notification } from '@/types';

interface ModalButtonProps {
  noti: Notification;
}

const ModalButton = ({ noti }: ModalButtonProps) => {
  const confirm = useConfirm();

  return (
    <Tooltip title="상세보기" placement="top">
      <IconButton
        onClick={() => {
          confirm({
            title: `${noti.PK.split('#')[1]} 수정하기`,
            content: <UpdateModal noti={noti} />,
            cancellationButtonProps: {
              sx: {
                display: 'none',
              },
            },
            confirmationButtonProps: {
              sx: {
                display: 'none',
              },
            },
          });
        }}
      >
        <CreateOutlined color="info" />
      </IconButton>
    </Tooltip>
  );
};

export default ModalButton;
