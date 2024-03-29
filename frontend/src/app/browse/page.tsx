"use client";
import Layout from "../../lib/components/AppLayout";
import ToolBar from "../../lib/components/ToolBar";
import Box from "@mui/joy/Box";
import Container from "@mui/joy/Container";

type UploadProps = {
  children: React.ReactNode
}
const UploadPane = ({children}: UploadProps) =>  {
  return <>
    {children}
  </> 
}

const BrowseView = () => {
  return <Layout>
    <UploadPane>
      <div className="">
        asdf
        </div> 
    </UploadPane>
  </Layout>;
};

export default BrowseView;
