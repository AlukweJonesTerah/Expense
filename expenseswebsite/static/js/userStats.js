const getHumanMonth = (m) => {
    const [_, month, __] = new Date(new Date().getFullYear(), m - 1, 1).toDateString().split(" ");
    return month;
};

const updateTopMonthsUI = (topMonth, type) => {
    const monthKey = Object.keys(topMonth)[0];
    const monthValue = Object.values(topMonth)[0];

    if (type === "expenses") {
        document.querySelector(".expense-top-month").textContent = getHumanMonth(monthKey);
        document.querySelector(".expense-top-month-value").textContent = monthValue;
    } else {
        document.querySelector(".income-top-month").textContent = getHumanMonth(monthKey);
        document.querySelector(".income-top-month-value").textContent = monthValue;
    }
};

const updateThisMonthUI = (data = [], type = "expenses") => {
    const currentMonthNumber = new Date().getMonth() + 1;

    const currentMonthData = data.find((item) => {
        // Implement your logic to find the current month data here
        return item;
    });

    const monthKey = Object.keys(currentMonthData)[0];
    const monthValue = Object.values(currentMonthData)[0];

    if (type === "expenses") {
        document.querySelector(".expense-this-month").textContent = getHumanMonth(monthKey);
        document.querySelector(".expense-this-month-value").textContent = monthValue;
    } else {
        document.querySelector(".income-this-month").textContent = getHumanMonth(monthKey);
        document.querySelector(".income-this-month-value").textContent = monthValue;
    }
};

const formatStats = (data = {}, type = "expenses") => {
    const monthData = data.months;
    const vals = Object.values(monthData);
    const s = vals.map((item, i) => ({ [i + 1]: item }));

    const sorted = s.sort((a, b) => (Object.values(a)[0] > Object.values(b)[0] ? -1 : 1));
    const topMonth = sorted[0];

    if (type === "expenses") {
        updateThisMonthUI(s, "expenses");
    }
    if (type === "income") {
        updateThisMonthUI(s, "income");
    }

    updateTopMonthsUI(topMonth, type);
};

const setGraphs = (data) => {
    // Implement your logic to set graphs based on the data
};

const fetchData = async () => {
    try {
        const responses = await Promise.all([
            fetch("/expense_summary_rest").then((res) => res.json()),
            fetch("/last_3months_stats").then((res) => res.json()),
            fetch("/income/income_sources_data").then((res) => res.json()),
            fetch("/income/income_summary_rest").then((res) => res.json()),
        ]);

        const [thisYearExpenses, expenseCategories, incomeSources, thisYearIncome] = responses;
        formatStats(thisYearExpenses.this_year_expenses_data, "expenses");
        formatStats(thisYearIncome.this_year_income_data, "income");
        setGraphs(responses);
    } catch (error) {
        console.log("An error occurred:", error);
    }
};

window.onload = () => fetchData();
