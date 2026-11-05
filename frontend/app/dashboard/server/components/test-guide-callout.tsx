import { motion } from "motion/react";
import { PolicyCallout } from "@/components/policy";
import Link from "next/link";
import routeMap from "@/constants/route-map";

export default function TestGuideCallout() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.35, duration: 0.4 }}
    >
      <PolicyCallout
        variant="warning"
        title="‘테스트 알림 전송에 실패했습니다’라고 나와요"
      >
        <ul className="mb-0 list-disc pl-5">
          <li>
            <Link
              href={routeMap.DOCS.INSTALLATION}
              className="underline hover:text-primary"
            >
              시작하기 문서
            </Link>
            의 채널 권한 설정을 보고, 치직 봇에게 필요한 권한이 있는지 확인해
            주세요.
          </li>
        </ul>
      </PolicyCallout>
    </motion.div>
  );
}
