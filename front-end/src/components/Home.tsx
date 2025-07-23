import { useNavigate } from "react-router-dom";
import { Button } from "@mui/material";

export function Home() {
  const navigate = useNavigate();
  return (
    <>
      <h1>Welcome to BxOCRui</h1>
      <p>This is a simple OCR software using PaddlePaddle.</p>
      <div>
        <Button
          variant="contained"
          onClick={() => navigate("/invoice", { replace: false })}
        >
          添加发票
        </Button>
      </div>
    </>
  );
}
