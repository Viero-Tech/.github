-- CreateTable
CREATE TABLE "Widget" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "stock" INTEGER NOT NULL,

    CONSTRAINT "Widget_pkey" PRIMARY KEY ("id")
);
