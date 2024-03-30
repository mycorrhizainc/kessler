"use client";

import { useRouter } from "next/router";

const LinkSlugView = () => {
  const router = useRouter();
  const slug = router.query.slug;
  return <p>Link ID: {slug}</p>;
};

export default LinkSlugView;
