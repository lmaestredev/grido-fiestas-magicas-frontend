import ConfirmationSection from "~/components/ConfirmationSection";

interface ConfirmationPageProps {
  searchParams: Promise<{
    parentesco?: string;
    nombre?: string;
  }> | {
    parentesco?: string;
    nombre?: string;
  };
}

export default async function ConfirmationPage({
  searchParams,
}: ConfirmationPageProps) {
  // Manejar tanto Promise como objeto directo (compatibilidad con Next.js 15+ y 16)
  const params = searchParams instanceof Promise 
    ? await searchParams 
    : searchParams;

  // Decodificar los parámetros de la URL y manejar valores vacíos
  const parentesco = params.parentesco && params.parentesco.trim() !== ""
    ? decodeURIComponent(params.parentesco) 
    : undefined;
  const nombre = params.nombre && params.nombre.trim() !== ""
    ? decodeURIComponent(params.nombre) 
    : undefined;

  return (
    <ConfirmationSection
      parentesco={parentesco}
      nombre={nombre}
    />
  );
}

