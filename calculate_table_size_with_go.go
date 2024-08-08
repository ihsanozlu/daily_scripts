package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"

	_ "github.com/lib/pq"
)

// Database configuration
const (
	dbHost     = "dbhost"
	dbPort     = 5432 // Change to your PostgreSQL port if different
	dbUser     = "postgres"
	dbPassword = "password"
	dbName     = "dbname"
)

func main() {
	// Step 1: Open the CSV file
	filePath := "thecsvfilepath"
	file, err := os.Open(filePath)
	if err != nil {
		log.Fatal("Error opening CSV file:", err)
	}
	defer file.Close()

	// Step 2: Connect to the PostgreSQL server
	dbInfo := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable", dbHost, dbPort, dbUser, dbPassword, dbName)
	db, err := sql.Open("postgres", dbInfo)
	if err != nil {
		log.Fatal("Error connecting to the database:", err)
	}
	defer db.Close()

	// Create a new CSV file to write the updated data
	newFilePath := "newcsvfilepath"
	newFile, err := os.Create(newFilePath)
	if err != nil {
		log.Fatal("Error creating new CSV file:", err)
	}
	defer newFile.Close()

	// Initialize a CSV writer to write to the new CSV file
	writer := csv.NewWriter(newFile)
	defer writer.Flush()

	// Step 3: Read the CSV file and execute the query for each row
	reader := csv.NewReader(file)
	reader.Comma = ';'
	for {
		// Read a row from the CSV file
		row, err := reader.Read()
		if err == io.EOF {
			break // End of file
		} else if err != nil {
			log.Println("Error reading CSV row:", err)
			continue
		}

		// Check if the row has at least two columns (A and B)
		if len(row) < 2 {
			log.Println("Row does not have enough columns:", row)
			continue
		}

		// Extract values from the row
		A := row[0]
		B := row[1]

		// Step 4: Execute the query and get the count
		query := fmt.Sprintf("SELECT COUNT(*) FROM %s.%s", A, B)
		var count int
		err = db.QueryRow(query).Scan(&count)
		if err != nil {
			log.Printf("Error executing query for %s.%s: %s", A, B, err)
			continue
		}

		// Update the C column in the row with the count
		result := make([]string, 0, 4)
		result = append(result, row...)
		result = append(result, strconv.Itoa(count))

		// Write the updated row to the new CSV file
		err = writer.Write(result)
		if err != nil {
			log.Println("Error writing to CSV file:", err)
		}
	}
}

