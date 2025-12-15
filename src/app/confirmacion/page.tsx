import ConfirmationSection from "~/components/ConfirmationSection";

interface ConfirmationPageProps {
  searchParams: {
    parentesco?: string;
    nombre?: string;
  };
}

export default function ConfirmationPage({
  searchParams,
}: ConfirmationPageProps) {
  return (
    <ConfirmationSection
      parentesco={searchParams.parentesco}
      nombre={searchParams.nombre}
    />
  );
}

