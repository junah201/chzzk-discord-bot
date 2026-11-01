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
        title="‘해당 치지직 채널을 찾을 수 없습니다’라고 나와요"
      >
        <ul className="mb-0 list-disc pl-5">
          <li>ID에 공백이나 특수문자가 들어가지 않았는지 확인해 주세요.</li>
          <li>
            한 번도 방송하지 않은 채널은 등록할 수 없습니다.
          </li>
          <li>
            오래 방송하지 않은 채널은 방송을 한 번 켜면 등록할 수 있습니다.
          </li>
        </ul>
      </PolicyCallout>
    </motion.div>
  );
}
