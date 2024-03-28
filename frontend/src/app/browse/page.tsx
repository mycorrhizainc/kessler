"use client";
import Layout from "../../lib/components/AppLayout";
import ToolBar from "../../lib/components/ToolBar";
import Box from "@mui/joy/Box";
import Container from "@mui/joy/Container";

const BrowseView = () => {
  return <Layout>
    <div className="bg-slate-100 container center flex flex-column">
      <Box className="grow shrink-8"
      sx={{
        
      }}>
        things
        <br />
        stuff
        <br />
        aand the like
      </Box>
    </div>
  </Layout>;
};

export default BrowseView;
