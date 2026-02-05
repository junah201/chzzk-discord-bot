import { motion } from "motion/react";
import { PolicyCallout } from "@/components/policy";

export default function SetupGuideCallout() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15, duration: 0.4 }}
    >
      <PolicyCallout
        variant="warning"
        title="해당 치지직의 채널을 찾을 수 없다고 떠요"
      >
        <ul className="mb-0 list-disc pl-5">
          <li>ID에 공백이나 특수문자가 포함되지 않았는지 확인해주세요.</li>
          <li>
            방송 기록이 아예 없는 신설 채널은 치지직 API 제한으로 인해 검색되지
            않을 수 있습니다.
          </li>
          <li>
            휴면 채널의 경우, 방송을 한 번 시작하면 정상적으로 인식됩니다.
          </li>
        </ul>
      </PolicyCallout>
    </motion.div>
  );
}
